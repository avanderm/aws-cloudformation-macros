PROJECT=cloudformation

ifndef ENVIRONMENT
	ENVIRONMENT=$(USER)
endif
ifndef MACRO_NAME
	$(info WARNING: MACRO_NAME has to be passed as a parameter)
endif

STACK=$(DOMAIN)-macro-$(MACRO_NAME)-$(ENVIRONMENT)

BUILD_DIR=_build

CF_TEMPLATE=template.yml
CF_PACKAGED=packaged.yml
CF_LOCATION=$(ARTIFACT_BUCKET)

build:
	docker build \
		--build-arg "MACRO_PATH=$(MACRO_PATH)" \
		--build-arg "MACRO_NAME=$(MACRO_NAME)" \
		-t $(MACRO_PATH)-$(ENVIRONMENT) .

deploy:	clean build
	docker run \
		-e "ENVIRONMENT=$(ENVIRONMENT)" \
		-e "MACRO_NAME=$(MACRO_NAME)" \
		-v $(HOME)/.aws:/root/.aws \
		--rm \
		-it $(MACRO_PATH)-$(ENVIRONMENT) make cloudformation-package cloudformation-deploy

cloudformation-package:
	aws cloudformation package \
		--template-file $(CF_TEMPLATE) \
		--s3-bucket $(CF_LOCATION) \
		--s3-prefix packages \
		--output-template-file $(CF_PACKAGED)

cloudformation-deploy:
	aws cloudformation deploy \
		--template-file $(CF_PACKAGED) \
		--stack-name $(STACK) \
		--capabilities CAPABILITY_IAM \
		--parameter-overrides \
			Environment=$(ENVIRONMENT) \
			MacroName=$(MACRO_NAME) \
		--tags \
			Environment=$(ENVIRONMENT) \
			Project=$(PROJECT)

delete:
	aws cloudformation delete-stack \
		--stack-name $(STACK)

clean:
	find . -name "*.pyc" -exec rm -f {} \;