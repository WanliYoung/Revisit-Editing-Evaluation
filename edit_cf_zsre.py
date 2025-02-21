from easyeditor import ROMEHyperParams, BaseEditor, MEMITHyperParams, MENDHyperParams, FTHyperParams, R_ROMEHyperParams, GraceHyperParams, WISEHyperParams
import json


# load data for editing
# data for zsre
# data = json.load(open("./data/zsre_eval_10000.json", 'r', encoding='utf-8')) 

# data for counterfact
data = json.load(open("./data/counterfact-edit.json", 'r', encoding='utf-8'))  

prompts = [d["prompt"] for d in data]  # "src" for zsre
target_new = [d["target_new"] for d in data]  # "alt" for zsre
subject = [d["subject"] for d in data]  # "subject" for zsre

rephrase_prompts = [d["rephrase_prompt"] for d in data]  # "rephrase" for zsre

locality_prompts = [d["locality_prompt"] for d in data]  # "loc" for zsre
locality_ans = [d["locality_ground_truth"] for d in data]  # "loc_ans" for zsre

locality_inputs = {
    'neighborhood': {
        'prompt': locality_prompts,
        'ground_truth': locality_ans
    },
}

# loc prompts for wise
# loc_data = json.load(open(f'./data/zsre_mend_train.json', 'r', encoding='utf-8'))[:10000]
# loc_prompts = [edit_data_['loc'] + ' ' + edit_data_['loc_ans'] for edit_data_ in loc_data]

hparams = FTHyperParams.from_hparams('./hparams/FT/llama-7b')  
editor = BaseEditor.from_hparams(hparams)

metrics, edited_model, _ = editor.edit(
    prompts=prompts,
    target_new=target_new,
    subject=subject,
    rephrase_prompts=rephrase_prompts,
    locality_inputs=locality_inputs,
    # loc_prompts=loc_prompts,  # for wise
    sequential_edit=False,  # True for sequential editing
)

# dump results to json file
# output_file = "output/output.json"
# with open(output_file, 'w') as f:
#     json.dump(metrics, f, indent=4)