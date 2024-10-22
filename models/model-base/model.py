#%%
def load_model():
    from transformers import AutoTokenizer, AutoModelForCausalLM

    tokenizer = AutoTokenizer.from_pretrained("asm3515/llama-3.2-isntruct-3B")
    model = AutoModelForCausalLM.from_pretrained("asm3515/llama-3.2-isntruct-3B")

    # Model has been pushed to huggingface making code clean and skipping large files to more optimised workload.

    # This function returns model which will be used for further finegrain and finetunning for RAG
    return(tokenizer,model)

