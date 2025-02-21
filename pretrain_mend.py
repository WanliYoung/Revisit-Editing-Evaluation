from easyeditor import MENDTrainingHparams, CounterFactDataset, EditTrainer, ZsreDataset
# Loading config 
hparams = MENDTrainingHparams.from_hparams('./hparams/TRAINING/MEND/mistral-7b.yaml')

# Preparing data
train_ds = ZsreDataset("./data/zsre/zsre_mend_train.json", config=hparams)
eval_ds = ZsreDataset("./data/zsre/zsre_mend_eval.json", config=hparams)

# Training editor model
trainer = EditTrainer(
    config=hparams,
    train_set=train_ds,
    val_set=eval_ds
)

trainer.run()