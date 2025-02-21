from easyeditor import BaseEditor, FTHyperParams, MENDHyperParams, ROMEHyperParams, R_ROMEHyperParams, MEMITHyperParams, GraceHyperParams, WISEHyperParams
import json


# load data for editing
data = json.load(open("./data/QAEdit/QAEdit.json", 'r', encoding='utf-8'))

prompts = [d["prompt"] for d in data]  
target_new = [d["target"] for d in data]  
subject = [d["subject"] for d in data]

rephrase_prompts = [d["rephrase"] for d in data]
locality_prompts = [d["locality"][0]["loc"] for d in data]
locality_ans = [d["locality"][0]["loc_ans"] for d in data]

locality_inputs = {
    'neighborhood': {
        'prompt': locality_prompts,
        'ground_truth': locality_ans
    },
}

# loc prompts for wise
# loc_data = json.load(open(f'./data/zsre/zsre_mend_train.json', 'r', encoding='utf-8'))[:10]
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