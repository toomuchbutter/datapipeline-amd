cd /workspace/shared/datapipeline-amd/aiis-data-layer
./launch_pipeline.sh

huggingface-cli download Qwen/Qwen3-4B --local-dir ./my-qwen-model

Run this command before working with AI Agents
`vllm serve Qwen/Qwen3-4B --served-model-name Qwen3-4B --api-key abc-123 --port 8000 --enable-auto-tool-choice --tool-call-parser hermes --trust-remote-code --max_model_len 24272`
