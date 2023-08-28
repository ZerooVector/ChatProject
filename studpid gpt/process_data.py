with open('data/train4.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
#print(lines)
train_datas = []
temp_data = ''
for line in lines:
    if line != '\n':
        line = line.strip('')
        print(line)
        temp_data += (line + '\t')
    else:
        train_datas.append(temp_data)
        temp_data = ''
print(train_datas)
with open('data/dataset.txt', 'w', encoding='utf-8') as f:
    for train_data in train_datas:
        if len(train_data)<1024:
            f.write(train_data + '\n')
