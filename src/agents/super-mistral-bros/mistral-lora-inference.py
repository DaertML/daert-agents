import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

def respond(query):
    eval_prompt = """Patient's Query:\n\n {} ###\n\n""".format(query)
    model_input = tokenizer(eval_prompt, return_tensors="pt").to("cuda")
    output = ft_model.generate(input_ids=model_input["input_ids"].to("cuda"),
                           attention_mask=model_input["attention_mask"], 
                           max_new_tokens=125, repetition_penalty=1.15)
    result = tokenizer.decode(output[0], skip_special_tokens=True).replace(eval_prompt, "")
    return result

base_model_id = "mistralai/Mistral-7B-v0.1"
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

base_model = AutoModelForCausalLM.from_pretrained(
    base_model_id,  # Mistral, same as before
    quantization_config=bnb_config,  # Same quantization config as before
    device_map="auto",
    trust_remote_code=True
)

tokenizer = AutoTokenizer.from_pretrained(base_model_id, add_bos_token=True, trust_remote_code=True)


from peft import PeftModel

ft_model = PeftModel.from_pretrained(base_model, "/home/pc/Desktop/LLaMA-Factory/saves/Mistral-7B/lora/train_2024-03-25-22-22-32")

res = respond("I have headache")
print(res)