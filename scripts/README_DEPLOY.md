Automated deployment helper

This folder contains helper scripts to automate environment setup and (optionally) start a model server.

Files:
- `deploy_windows.ps1` - PowerShell script for Windows. Usage:
  - Open PowerShell, allow script execution for the session:
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
    .\scripts\deploy_windows.ps1 -ModelService none
    # or start vllm: .\scripts\deploy_windows.ps1 -ModelService vllm
    ```

- `deploy_linux.sh` - Unix shell script. Usage:
  ```bash
  chmod +x scripts/deploy_linux.sh
  ./scripts/deploy_linux.sh none
  # or start vllm: ./scripts/deploy_linux.sh vllm
  ```

Notes and recommendations:
- These scripts create a local `.venv` and install dependencies from `requirements.txt`.
- They will not auto-download large models. Follow README steps to obtain or configure model paths.
- For vLLM/SGLang model servers, the script attempts to run the Python entrypoints (requires those packages installed and model available).
- If you prefer Docker-based deployment, follow README model provider instructions for container images.

If you want, I can:
- Add a `Makefile` with targets `setup`, `start-vllm`, `start-sglang`.
- Create a `docker-compose.yml` for containerized model + agent orchestration (requires decision on which model infra to support).
