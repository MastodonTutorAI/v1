def load_model():
    from transformers import AutoTokenizer, AutoModelForCausalLM

    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-1B-Instruct")
    model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-1B-Instruct")

    # Model has been pushed to huggingface making code clean and skipping large files to more optimised workload.

    # This function returns model which will be used for further finegrain and finetunning for RAG
    return(tokenizer,model)