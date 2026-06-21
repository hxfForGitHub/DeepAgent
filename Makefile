.PHONY: all test run help

all: help

run:
	python run_agent.py

test:
	python -m pytest tests/unit_tests/ -v

help:
	@echo '----'
	@echo 'run    - 运行 my_agent1 交互式对话'
	@echo 'test   - 运行单元测试'
