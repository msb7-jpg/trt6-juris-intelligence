os containers estao subindo

api
ingestion
minio
postgres
rabbitmq

porem os containers que dependem do celery e tentam se conectar ao brooker em rabbitmq, nao estao conseguindo se conectar com sucesso, preciso diagnosticar o problema para que eles consigam se conectar e todo o fluxo rode normalmente sem interrupções, para isso investigue os logs dos containers e rode novamente essses servicos especificos ate confirmar que eles conseguiram se conectar