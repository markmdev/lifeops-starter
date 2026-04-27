PYTHON ?= python3
TMP_INSTALL ?= /tmp/lifeops-starter-e2e

.PHONY: test privacy no-symlinks e2e-minimal clean-e2e

test:
	$(PYTHON) -m unittest discover -s tests

privacy:
	$(PYTHON) .agents/skills/setup-lifeops/scripts/privacy_scan.py --mode public-repo --root .

no-symlinks:
	@test -z "$$(find . -type l -print)" || (find . -type l -print && exit 1)

e2e-minimal: clean-e2e
	$(PYTHON) .agents/skills/setup-lifeops/scripts/install_workspace.py --starter . --workspace $(TMP_INSTALL) --answers tests/fixtures/answers.minimal.json
	$(PYTHON) .agents/skills/setup-lifeops/scripts/verify_workspace.py --workspace $(TMP_INSTALL)

clean-e2e:
	rm -rf $(TMP_INSTALL)
