.PHONY: up down build smoke seed demo student baseline compare test short local agent sessions episodes heartbeat compiled forget golden ui report student-report golden-report clean

build:
	docker compose build

up:
	docker compose up -d redis qdrant

down:
	docker compose down

# app runs on a remote DOCKER_HOST with no source bind-mount, so every
# app-invoking target rebuilds first (cheap: cached pip layer, only the
# code layer re-copies) to make sure local edits are actually picked up.
smoke: build
	docker compose run --rm app python -m src.smoke

seed: build
	docker compose run --rm app python -m src.seed

demo: build
	docker compose run --rm app python -m src.evaluate --impl reference --reuse-seeded

student: build
	docker compose run --rm app python -m src.evaluate --impl student --reuse-seeded

baseline: build
	docker compose run --rm app python -m src.evaluate --impl no_memory

compare: build
	docker compose run --rm app python -m src.compare_reports

test: build
	docker compose run --rm app pytest -q

short: build
	docker compose run --rm app python -m src.demo_short_term

local: build
	docker compose run --rm app python -m src.local_baseline

agent: build
	docker compose run --rm app python -m src.demo_agent --impl reference --reset

sessions: build
	docker compose run --rm app python -m src.demo_sessions

episodes: build
	docker compose run --rm app python -m src.episodic_maintenance

heartbeat: build
	docker compose run --rm app python -m src.heartbeat --dry-run

compiled: build
	docker compose run --rm app python -m src.compiled_kb --reset

forget: build
	docker compose run --rm app python -m src.forget --user-id minh-lab17

golden: build
	docker compose run --rm app python -m src.evaluate --impl student --reuse-seeded --golden

ui: build
	docker compose run --rm --service-ports -e PYTHONPATH=/workspace app streamlit run src/demo_ui.py --server.address 0.0.0.0 --server.port 8501

# Build colorful HTML reports from every reports/*benchmark*.json (+ run log if present).
report: build
	docker compose run --rm app python -m src.report_html --all --log reports/run.log

# Run the student benchmark, capture the run log, then render the HTML report.
student-report: build
	docker compose run --rm app sh -c "python -m src.evaluate --impl student --reuse-seeded 2>&1 | tee reports/run.log && python -m src.report_html --input reports/benchmark.json --log reports/run.log"

# Run the golden benchmark, capture the run log, then render the HTML report.
golden-report: build
	docker compose run --rm app sh -c "python -m src.evaluate --impl student --reuse-seeded --golden 2>&1 | tee reports/run.log && python -m src.report_html --input reports/golden_benchmark.json --log reports/run.log"

clean:
	docker compose down -v
	rm -f reports/benchmark*.json reports/benchmark*.md reports/comparison.md reports/golden* reports/*.html reports/run.log
