# Pixel Prompt JS

**Pixel Prompt** is an app made with React Native built using Expo. It uses the Hugging Face Inference API along with  diffusion models to create images. An explanation of some of the componenets and deployment architectures: [Cloud Bound](https://medium.com/@HatmanStack/cloud-bound-react-native-and-fastapi-ml-684a658f967a).  This is the AWS Lambda backend for the JS implementation.  It can be built and deployed for web, android, or ios.

## Preview :zap:

To preview the application visit the hosted version on AWS [here](https://production.d2iujulgl0aoba.amplifyapp.com/).

## Prerequisites

Before running this application locally, ensure that you have the following dependencies installed on your machine:

- Python
- pip
- [groq](https://groq.com/) account

## Installation :hammer:

To install and run the application:
 
 ```shell
 pip install -r requirements.txt --target .
 ```
Then zip all the files in the directory and upload to your Lambda function with the correct version of python.
Include these in the environment variables of your lambda.

   ```shell
  AWS_ID=<ID>
  AWS_SECRET=<secret>
  GROQ_API_KEY=<key>
  HF_TOKEN=<token>
  HF_HOME=/tmp/huggingface
   ```

## Models :sparkles:

All the models are opensource and available on HuggingFace.
       
### Diffusion

- **Random**
- **stabilityai/stable-diffusion-3.5**
- **OpenAI Dalle3**
- **AWS Nova Canvas**
- **black-forest-labs/FLUX**
- **stabilityai/stable-diffusion-xl-base-1.0**
- **nerijs/pixel-art-xl**
- **Fictiverse/Voxel_XL_Lora**
- **gsdf/Counterfeit-V2.5**

### Prompts

- **llama-3.1-8b-instant**
- **Gustavosta/MagicPrompt-Stable-Diffusion**

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments :trophy:

<p align="center">This application is using the HuggingFace Inference API, provided by <a href="https://huggingface.co">HuggingFace</a> </br><img src="https://github.com/HatmanStack/pixel-prompt-backend/blob/main/logo.png" alt="Image 4"></p>

