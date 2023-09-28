from base_setting import *
import os
import pytest
import shutil
import asyncio
from GeneralAgent.agent import Agent
from GeneralAgent.tools import Tools, scrape_web

workspace = './data/test_workspace'

@pytest.mark.asyncio
async def test_math():
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = Agent(workspace=workspace)
    result = ''
    async def _output_recall(token):
        if token is not None:
            nonlocal result
            result += token
            print(token, end='', flush=True)
    for_node_id = await agent.run('calculate 0.99 ** 1000', output_recall=_output_recall)
    assert '4.317124741065786e-05' in result
    assert for_node_id == None

@pytest.mark.asyncio
async def test_write_file():
    target_path = './data/a.txt'
    if os.path.exists(target_path):
        os.remove(target_path)
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = Agent(workspace=workspace)
    result = ''
    async def _output_recall(token):
        if token is not None:
            nonlocal result
            result += token
            print(token, end='', flush=True)
    for_node_id = await agent.run('Write the description of Chengdu to the file ./data/a.txt', output_recall=_output_recall)
    assert for_node_id == None
    assert os.path.exists(target_path)
    with open(target_path, 'r') as f:
        content = f.read()
        assert 'Chengdu' in content
    if os.path.exists(target_path):
        os.remove(target_path)

@pytest.mark.asyncio
async def test_read_file():
    content = """Chengdu, the capital of China's southwest Sichuan Province, is famed for being the home of cute giant pandas. Apart from the Panda Research base, Chengdu has a lot of other attractions. It is known for its spicy Sichuan cuisine and ancient history, including the site of the ancient Jinsha civilization and the Three Kingdoms-era Wuhou Shrine. The city also features beautiful natural landscapes such as Mount Qingcheng and the Dujiangyan Irrigation System, both UNESCO World Heritage Sites."""
    target_path = './data/b.txt'
    if os.path.exists(target_path):
        os.remove(target_path)
    with open(target_path, 'w') as f:
        f.write(content)
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = Agent(workspace=workspace)
    result = ''
    async def _output_recall(token):
        if token is not None:
            nonlocal result
            result += token
            print(token, end='', flush=True)
    for_node_id = await agent.run('what is in ./data/b.txt', output_recall=_output_recall)
    assert 'Mount Qingcheng' in result
    assert for_node_id == None
    if os.path.exists(target_path):
        os.remove(target_path)

@pytest.mark.asyncio
async def test_tool_use():
    if os.path.exists(workspace): shutil.rmtree(workspace)
    agent = Agent(workspace=workspace, tools=Tools([scrape_web]))
    result = ''
    async def _output_recall(token):
        if token is not None:
            nonlocal result
            result += token
            print(token, end='', flush=True)
    for_node_id = await agent.run("what's the tiltle of web page https://tongtianta.ai ?", output_recall=_output_recall)
    assert 'AI' in result
    assert for_node_id == None

@pytest.mark.asyncio
async def test_bash_interperter():
    pass

if __name__ == '__main__':
    # asyncio.run(test_math())
    # asyncio.run(test_write_file())
    # asyncio.run(test_read_file())
    asyncio.run(test_tool_use())