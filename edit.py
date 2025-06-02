import os.path
import json
import argparse

from easyeditor import (
    FTHyperParams,
    MENDHyperParams,
    ROMEHyperParams,
    R_ROMEHyperParams,
    MEMITHyperParams,
    GraceHyperParams,
    WISEHyperParams,
    BaseEditor,
    summary_metrics,
)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--editing_method', required=True, type=str)
    parser.add_argument('--hparams_dir', required=True, type=str)
    parser.add_argument('--data_path', required=True, type=str)
    parser.add_argument('--datatype', default=True,type=str)
    parser.add_argument('--ds_size', default=10, type=int)
    parser.add_argument('--sequential_edit', default='False', type=str)
    parser.add_argument('--batch_edit', default='False', type=str)
    parser.add_argument('--evaluation_type', default='WILD', type=str)
    parser.add_argument('--context_type', default='question-only', type=str)
    parser.add_argument('--api_key', default=None, type=str)
    parser.add_argument('--output_dir', default='./outputs', type=str)

    args = parser.parse_args()

    if args.sequential_edit == "True" or args.sequential_edit == "true":
        sequential_edit = True
    else:
        sequential_edit = False

    if args.batch_edit == "True" or args.batch_edit == "true":
        batch_edit = True
    else:
        batch_edit = False

    if args.editing_method == 'FT':
        editing_hparams = FTHyperParams
    elif args.editing_method == 'MEND':
        editing_hparams = MENDHyperParams
    elif args.editing_method == 'ROME':
        editing_hparams = ROMEHyperParams
    elif args.editing_method == 'R-ROME':
        editing_hparams = R_ROMEHyperParams
    elif args.editing_method == 'MEMIT':
        editing_hparams = MEMITHyperParams
    elif args.editing_method == 'GRACE':
        editing_hparams = GraceHyperParams
    elif args.editing_method == 'WISE':
        editing_hparams = WISEHyperParams
    else:
        raise NotImplementedError

    # load and process data
    K = args.ds_size
    edit_data = json.load(open(os.path.join(args.data_path), 'r', encoding='utf-8'))[:K]
    loc_data = json.load(open(os.path.join('./data/zsre_mend_train_10000.json'), 'r', encoding='utf-8'))[:K]  # default loc data for WISE
    loc_prompts = [edit_data_['loc'] + ' ' + edit_data_['loc_ans'] for edit_data_ in loc_data]

    if args.datatype == 'counterfact':
        prompts = [edit_data_['prompt'] for edit_data_ in edit_data]
        subject = [edit_data_['subject'] for edit_data_ in edit_data]
        rephrase_prompts = [edit_data_['rephrase_prompt'] for edit_data_ in edit_data]
        target_new = [edit_data_['target_new'] for edit_data_ in edit_data]
        locality_prompts = [edit_data_['locality_prompt'] for edit_data_ in edit_data]
        locality_ans = [edit_data_['locality_ground_truth'] for edit_data_ in edit_data]
    elif args.datatype == 'zsre':
        prompts = [edit_data_['src'] for edit_data_ in edit_data]
        subject = [edit_data_['subject'] for edit_data_ in edit_data]
        rephrase_prompts = [edit_data_['rephrase'] for edit_data_ in edit_data]
        target_new = [edit_data_['alt'] for edit_data_ in edit_data]
        locality_prompts = [edit_data_['loc'] for edit_data_ in edit_data]
        locality_ans = [edit_data_['loc_ans'] for edit_data_ in edit_data]
    elif args.datatype == 'qaedit':
        prompts = [edit_data_['prompt'] for edit_data_ in edit_data]
        subject = [edit_data_['subject'] for edit_data_ in edit_data]
        rephrase_prompts = [edit_data_['rephrase'] for edit_data_ in edit_data]
        target_new = [edit_data_['target'] for edit_data_ in edit_data]
        locality_prompts = [edit_data_["locality"][0]["loc"] for edit_data_ in edit_data]
        locality_ans = [edit_data_["locality"][0]["loc_ans"] for edit_data_ in edit_data]

    locality_inputs = {
        'neighborhood':{
            'prompt': locality_prompts,
            'ground_truth': locality_ans
        },
    }

    hparams = editing_hparams.from_hparams(f'{args.hparams_dir}')
    # specify WILD evaluation and provide the api key for LLM-as-a-Judge
    hparams.evaluation_type = args.evaluation_type
    hparams.context_type = args.context_type
    hparams.api_key = args.api_key

    os.makedirs(args.output_dir, exist_ok=True)
    output_file = os.path.join(
        args.output_dir,
        f'{hparams.model_name.split("/")[-1]}_{args.editing_method}_N={args.ds_size}_Sequential={args.sequential_edit}_Batch={args.batch_edit}.json'
    )

    print("See results at: ", output_file)

    editor = BaseEditor.from_hparams(hparams)

    if batch_edit:
        metrics, edited_model, _ = editor.batch_edit(
            prompts=prompts,
            rephrase_prompts=rephrase_prompts,
            subject=subject,
            target_new=target_new,
            loc_prompts=loc_prompts,
            locality_inputs=locality_inputs,
        )
    else:
        metrics, edited_model, _ = editor.edit(
            prompts=prompts,
            rephrase_prompts=rephrase_prompts,
            subject=subject,
            target_new=target_new,
            loc_prompts=loc_prompts,
            locality_inputs=locality_inputs,
            sequential_edit=sequential_edit,
        )

    with open(output_file, 'w') as f:
        json.dump(metrics, f, indent=4)

    if len(metrics) > 0:
        summary_metrics(metrics)
