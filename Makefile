ifndef AWS_PROFILE
	AWS_PROFILE=default
endif
ifndef ARTIFACT_BUCKET
	$(info WARNING: ARTIFACT_BUCKET has to be passed as a parameter)
endif
ifndef MACRO_NAME
	$(info WARNING: MACRO_NAME has to be passed as a parameter)
endif

STACK=macro-$(MACRO_NAME)

BUILD_DIR=_build

CF_PACKAGED=packaged.yml
CF_LOCATION=$(ARTIFACT_BUCKET)

build:
	docker build \
		--build-arg "MACRO_PATH=$(MACRO_PATH)" \
		--build-arg "MACRO_NAME=$(MACRO_NAME)" \
		-t $(MACRO_PATH) .

bootstrap: clean build
	-docker run \
		-e "ARTIFACT_BUCKET=$(ARTIFACT_BUCKET)" \
		-e "AWS_PROFILE=$(AWS_PROFILE)" \
		-e "MACRO_NAME=SubReplicate" \
		-e "CF_TEMPLATE=bootstrap.yml" \
		-v $(HOME)/.aws:/root/.aws \
		--rm \
		-it substitution-replicate make cloudformation-package cloudformation-deploy

deploy:	clean build bootstrap
	docker run \
		-e "MACRO_NAME=$(MACRO_NAME)" \
		-e "AWS_PROFILE=$(AWS_PROFILE)" \
		-e "ARTIFACT_BUCKET=$(ARTIFACT_BUCKET)" \
		-e "CF_TEMPLATE=template.yml" \
		-v $(HOME)/.aws:/root/.aws \
		--rm \
		-it $(MACRO_PATH) make cloudformation-package cloudformation-deploy

cloudformation-package:
	aws cloudformation package \
		--profile $(AWS_PROFILE) \
		--template-file $(CF_TEMPLATE) \
		--s3-bucket $(CF_LOCATION) \
		--s3-prefix packages \
		--output-template-file $(CF_PACKAGED)

cloudformation-deploy:
	aws cloudformation deploy \
		--profile $(AWS_PROFILE) \
		--template-file $(CF_PACKAGED) \
		--stack-name $(STACK) \
		--capabilities CAPABILITY_IAM \
		--parameter-overrides \
			MacroName=$(MACRO_NAME)

delete:
	aws cloudformation delete-stack \
		--profile $(AWS_PROFILE) \
		--stack-name $(STACK)

clean:
	find . -name "*.pyc" -exec rm -f {} \;