from intrument_model import InstrumentClassification
from instrument_dataset import InstrumentDataModule
import pytorch_lightning as pl
from torch import cuda, jit
import config


if __name__ == "__main__":
    model = InstrumentClassification(num_labels=config.NUM_LABELS,
                                     learning_rate=config.LEARNING_RATE)
    
    trainer = pl.Trainer(accelerator="gpu" if cuda.is_available() else "cpu",
                         min_epochs=config.MIN_EPOCHS,
                         max_epochs=config.MAX_EPOCHS,
                         callbacks=[pl.callbacks.EarlyStopping(monitor='val_loss', patience=3, verbose=True, mode='min')])
    
    dm = InstrumentDataModule(batch_size=config.BATCH_SIZE,
                              data_path=config.DATA_PATH,)
    
    # trainer.tune(model, dm) # hyperparameter tuning
        
    trainer.fit(model, dm)
    trainer.validate(model, dm)
    script = model.to_torchscript()
    jit.save(script, "modelnew.pt")
    #trainer.test(model, dm)