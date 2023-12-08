FROM condaforge/miniforge3

RUN conda create -n esrgan python=3.10
RUN conda install pytorch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 pytorch-cuda=11.7 -c pytorch -c nvidia

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y # move to line 2

WORKDIR /app
ADD process_image.py bot.py token.txt ./
ADD RealESRGAN ./RealESRGAN
ADD inputs ./inputs
ADD weights ./weights

#CMD [ "/bin/bash"]
CMD [ "python", "bot.py"]