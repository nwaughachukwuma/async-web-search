dev:
	granian --interface asgi src/index:app --port 3535 --runtime-threads 4 \
		--loop uvloop \
		--runtime-mode mt \
		--reload-paths "src" \
		--reload

test:
	pytest -v tests/ --tb=short
