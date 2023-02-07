import ee

from dotenv import load_dotenv

import inputs
import processing
import export

def run(config: inputs.Config):

     load_dotenv()

     datas = inputs.setup_inputs(config)

     for data in datas:

          #Prep Images
          processing.batch_despckle(data, filter_size=1)
          processing.batch_register(data)

          # geneate samples
          processing.batch_generate_samples(data)

          # Run exports
          table_tasks = export.table_cloud_task(data)
          image_tasks = export.table_cloud_task(data)
          task_que = [*table_tasks, *image_tasks]
          export.export_tasks(task_que)
     return None