from harness.prompt import task_prompt
def test_contract():
 p=task_prompt('Do thing',100)
 assert 'vant agent' in p and 'Do not launch Chromium' in p and 'ground truth' in p and '100 steps' in p
