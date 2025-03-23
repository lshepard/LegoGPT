#!/usr/bin/zsh

ROOT_DIR="/data/apun"
args=(
    --model_name_or_path "meta-llama/Llama-3.2-1B-Instruct"

    # Dataset parameters
    --dataset_name "${ROOT_DIR}/StableText2Lego_combined_dummy"
    --dataloader_num_workers 4

    # Training parameters
    --per_device_train_batch_size 1
    --per_device_eval_batch_size 1
    --gradient_accumulation_steps 4
    --learning_rate 6e-5
    --lr_scheduler_type cosine
    --warmup_steps 100
    --num_train_epochs 5
    --save_steps 2000

    # Optimizations
    --bf16

    # LoRA parameters
    --use_peft
    --lora_r 32
    --lora_alpha 16
    --lora_dropout 0.05
    --lora_target_modules q_proj v_proj

    # Output parameters
    --output_dir "${ROOT_DIR}/finetuned_hf/Llama-3.2-1B-Instruct_finetuned_combined"
    --run_name "Llama-3.2-1B-Instruct_finetuned_combined"
    --report_to wandb
)

trl sft "${args[@]}"
