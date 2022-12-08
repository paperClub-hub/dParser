## 自定义数据集训练

### 1. 环境


`
事先安装paddlepaddle-gpu
pip install --upgrade pip
pip install  paddlenlp==2.4.2 -i https://mirrors.aliyun.com/pypi/simple/
`

### 2.数据标注及导出

` 参考：https://github.com/PaddlePaddle/PaddleNLP/tree/develop/model_zoo/uie

`

### 3. 训练：

`
export finetuned_model=./checkpoint/model_best

python finetune.py  \
    --device gpu \
    --logging_steps 10 \
    --save_steps 100 \
    --eval_steps 100 \
    --seed 42 \
    --model_name_or_path uie-base \
    --output_dir $finetuned_model \
    --train_path data/train.txt \
    --dev_path data/dev.txt  \
    --max_seq_length 512  \
    --per_device_eval_batch_size 16 \
    --per_device_train_batch_size  16 \
    --num_train_epochs 100 \
    --learning_rate 1e-5 \
    --label_names 'start_positions' 'end_positions' \
    --do_train \
    --do_eval \
    --do_export \
    --export_model_dir $finetuned_model \
    --overwrite_output_dir \
    --disable_tqdm True \
    --metric_for_best_model eval_f1 \
    --load_best_model_at_end  True \
    --save_total_limit 1 \

偷懒： python ./fine.py 
`


### 4. 导出torch模型

`
参考：uie_torch/convert.py

`