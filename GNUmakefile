ifndef SECRETS_REPO_DIR
	SECRETS_REPO_DIR = ~
endif

SECRETS_REPO_NAME = lucy-config
SECRETS_REPO_PATH = $(SECRETS_REPO_DIR)/$(SECRETS_REPO_NAME)
SETTINGS_PATH = ./config
CURRENT_BRANCH = $(shell git -C $(SECRETS_REPO_PATH) symbolic-ref --short HEAD)
CLONE_PATH = flask@vault.lib.uchicago.edu:/data/vault/flask/$(SECRETS_REPO_NAME)

.PHONY: secrets
secrets: update-secrets install

.PHONY: update-secrets
update-secrets:
	git -C $(SECRETS_REPO_PATH) pull origin $(CURRENT_BRANCH)

.PHONY: install
install: clean
	install -m 444 $(SECRETS_REPO_PATH)/local.py $(SETTINGS_PATH)

.PHONY: create-repo
create-repo:
	mkdir -p $(SECRETS_REPO_DIR)
	git -C $(SECRETS_REPO_DIR) clone $(CLONE_PATH)

.PHONY: clean
clean:
	$(RM) $(SETTINGS_PATH)/secrets.py || true
