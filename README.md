# Pixel Prompt JS

**Pixel Prompt** is an app made with React Native built using Expo. It uses the Hugging Face Inference API along with  diffusion models to create images. An explanation of some of the componenets and deployment architectures: [Cloud Bound](https://medium.com/@HatmanStack/cloud-bound-react-native-and-fastapi-ml-684a658f967a).  This is the AWS Lambda backend for the JS implementation.  It can be built and deployed for web, android, or ios.

## Preview :zap:

To preview the application visit the hosted version on AWS [here](https://production.d2iujulgl0aoba.amplifyapp.com/).

## Prerequisites

Before running this application locally, ensure that you have the following dependencies installed on your machine:

- Python 3.12
- pip
- [groq](https://groq.com/) account

## Installation :hammer:

To install and run the application:
 
 ```shell
 pip install -r requirements.txt --target .
 ```
Then zip all the files in the directory and upload to your Lambda function with the correct version of python.
Include these in the environment variables of your lambda.  Create two functions to account for size cap of individual lambda functions.

   ```shell
   AWS_ID=<ID>
   AWS_SECRET=<secret>
   GROQ_API_KEY=<key>
   HF_TOKEN=<token>
   GPC_API_KEY=<token>
   RECRAFT_API_KEY=<token>
   OPENAI_API_KEY=<token>
   STABILITY_API_KEY=<token>
   BFL_API_KEY=<token>
   GLOBAL_LIMIT=<number>
   IP_LIMIT=<number>
   ```

## Models :sparkles:

All the models are SOTA and some are available on HuggingFace.
       
### Diffusion

- **Stable Diffusion Large**
- **Stable Diffusion Turbo**
- **Black Forest Pro**
- **Black Forest Dev**
- **Recraft v3**
- **OpenAI Dalle3**
- **AWS Nova Canvas**
- **Gemini 2.0**
- **Imagen 3.0**

### Prompts

- **meta-llama/llama-4-maverick-17b-128e-instruct**

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments :trophy:

<p align="center">This application is using the HuggingFace Inference API, provided by <a href="https://huggingface.co">HuggingFace</a> </br><img src="https://github.com/HatmanStack/pixel-prompt-backend/blob/main/logo.png" alt="Image 4"></p>

