from pathlib import Path
import pandas
from os.path import join, exists, isfile, join
from os import listdir
import re

# Remove directory when creating articles
def remove_dir(directory):
  directory = Path(directory)
  if not directory.is_dir():
    return
  for item in directory.iterdir():
    if item.is_dir():
      remove_dir(item)
    else:
      item.unlink()
  directory.rmdir()

# Used by write_non_tweets
def convert_token_to_character_number(tokens, token, is_start):
  if token == 0:
    return 0
  if is_start:
    return sum(map(lambda x: len(x), tokens[0:token])) + token #Account for spaces
  else:
    return sum(map(lambda x: len(x), tokens[0:token])) + token-1 #Account for spaces

# Used to figure out the spans when writing non tweets
def get_nearest_token_span(seq_length, start, end, tokens):

  seg_start, seg_end = 0, 0

  span_length = end-start
  left_or_right = (seq_length - span_length) // 2
  at_left_edge = start-left_or_right < 0
  at_right_edge = end+left_or_right > len(tokens)

  if at_left_edge:
    right_dist = seq_length - start - span_length
    seg_end = min(len(tokens), end+right_dist)
    seg_start = 0
  elif at_right_edge:
    left_dist = seq_length - ((len(tokens) - end) + span_length)
    seg_start = max(0, start - left_dist)
    seg_end = len(tokens)
  else:
    seg_start = start-left_or_right
    seg_end = end + left_or_right
  
  return seg_start, seg_end 

# Create forward pass and meta files for aschern
def create_fp_and_meta_files(meta_file_path, fp_file_path, sentences, spans, tokens=[], sequence_length=-1):

  meta_df = pandas.DataFrame(columns=["sentence", "start", "end"])
  sentences = list(map(lambda x,y: (x,y[0],y[1]), sentences, spans))
  # Pad each sentence correctly so we maximize how much is fed into the model.
  # Write the token position in the padded sentence to the meta data file. This way we can 
  # keep track of what the actual base sentence we are working with is!
  with open(fp_file_path, "w") as fp_file:
    position = 0
    for sentence in sentences:
      if len(sentence[0]) <= 1:
        continue

      # No padding, so we just use given sentence tokens
      if sequence_length == -1:
        meta_data_content = sentence
        meta_df = meta_df.append({"sentence": meta_data_content[0], "start": meta_data_content[1], "end": meta_data_content[2]}, ignore_index=True)  
        fp_file.write(meta_data_content[0] + "\n")
      # Deal with padding
      else:

        # Get token level start and end in padded sentence
        token_start, token_end = get_nearest_token_span(sequence_length, sentence[1], sentence[2], tokens)

        # Get character level end points for padded sentences, and the offsets of these sentences
        start_pad = convert_token_to_character_number(tokens, token_start, is_start=True)
        end_pad = convert_token_to_character_number(tokens, token_end, is_start=False)
        start = convert_token_to_character_number(tokens, sentence[1], is_start=True)
        end = convert_token_to_character_number(tokens, sentence[2], is_start=False)

        # Write to metadata file
        meta_data_content = (str(sentence[0]), str(position+(start-start_pad)), str(position+(end-start_pad)))          
        meta_df = meta_df.append({"sentence": meta_data_content[0], "start": meta_data_content[1], "end": meta_data_content[2]}, ignore_index=True)
        fp_file.write(" ".join(tokens[token_start:token_end]) + "\n")
        position += (end_pad-start_pad + 1)

  meta_df.to_csv(meta_file_path)

# Check that the spans we have in meta data file can be mapped back to the original sentences we care about
def span_checksum(feedforward_file_path, meta_file_path, total, to_long):
  with open(feedforward_file_path, "r") as ff:
    feed_forward_file_contents = "".join([line for line in ff])
    df = pandas.read_csv(meta_file_path)
    for i in range(df.shape[0]):
      total += 1
      
      line = df["sentence"][i]
      start = df["start"][i]
      end = df["end"][i]
      
      start, end = int(start), int(end)
      line = line.split()
      if len(line) > 75:
        to_long += 1
        continue
      line = ' '.join(line)
      try:
        assert(feed_forward_file_contents[start:end].strip() == line)
      except:
        print(feedforward_file_path,end="")
        print("\nMeta data line: ")
        print(line)
        print("\n\nFeed forward file associated line: ")
        print(feed_forward_file_contents[start:end])
        raise Exception()
  return total, to_long

# Used for checksum
def check_files(folder):

  total, to_long = 0, 0
  ff_files = [f for f in listdir(folder) if isfile(join(folder, f))]
  for i in range(len(ff_files)):
    
    if re.search("tweet", ff_files[i]):
      continue

    ff_file_path = join(folder, ff_files[i])
    meta_file_path = join(folder, "meta", ff_files[i][:-4] + ".csv").replace(" ", "_")

    assert(exists(ff_file_path)), ff_file_path
    assert(exists(meta_file_path)), meta_file_path

    try:
      total, to_long = span_checksum(ff_file_path, meta_file_path, total, to_long)
    except:
      return total, to_long
  print("passed...")
  return total, to_long 