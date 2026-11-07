import tiktoken

def define_token(phrase):
    encoding = tiktoken.encoding_for_model("gpt-4.1-mini")
    tokens = encoding.encode(phrase)
    
    print(f"Tokens for {phrase}: {tokens}")

    for token_id in tokens:
        token_text = encoding.decode([token_id])
        print(f"{token_id} = {token_text}")

    return tokens, encoding

define_token("Hello, my name is Dave. This is just a bunch of random text and misspelllllled wrds to see how otokenization works. I am going to keep typing until I run out of ideas. I will also include some numbers like 1234567890 and some special characters like !@#$%^&*()_+[]{}|;:',.<>/?`~ to see how they are tokenized. Let's see if this is enough text to test the tokenization process thoroughly.")