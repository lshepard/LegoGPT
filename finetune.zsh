#!/usr/bin/zsh

# Usage: ./finetune.zsh [RUN_NAME] [DATASET_NAME] [HF_TOKEN]

ROOT_DIR="/grogu/user/apun"
RUN_NAME="${1}"
DATASET_NAME="${2}"

export HF_HOME="${ROOT_DIR}/.cache/huggingface"
export HF_TOKEN="${3}"

args=(
    --model_name_or_path "${ROOT_DIR}/checkpoints_hf/meta-llama/Llama-3.2-1B-Instruct" # LLaMA model with modified tokenizer - no cutoff date system message
    --do_train
    --eval_strategy steps

    # Dataset parameters
    --dataset_name "${ROOT_DIR}/${DATASET_NAME}"
    --dataloader_num_workers 4
    --max_length 8192

    # Training parameters
    --per_device_train_batch_size 2
    --per_device_eval_batch_size 2
    --gradient_accumulation_steps 4
    --learning_rate 0.002
    --lr_scheduler_type cosine
    --warmup_steps 100
    --num_train_epochs 3
    --eval_steps 250
    --save_steps 500
    --load_best_model_at_end

    # Optimizations
    --bf16

    # LoRA parameters
    --use_peft
    --lora_r 32
    --lora_alpha 16
    --lora_dropout 0.05
    --lora_target_modules q_proj v_proj

    # Output parameters
    --output_dir "${ROOT_DIR}/finetuned_hf/${RUN_NAME}"
    --run_name "${RUN_NAME}"
    --report_to wandb
)

trl sft "${args[@]}"
