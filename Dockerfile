FROM lambci/lambda:build-python3.7

ENV BUILD_DIR _build
ARG MACRO_PATH
ARG MACRO_NAME
RUN mkdir -p ${BUILD_DIR}

# add an empty versions file in case none is present
RUN touch ${BUILD_DIR}/versions.yml
ADD ${MACRO_PATH} ${BUILD_DIR}
ADD logger.py ${BUILD_DIR}/src

RUN pip install --upgrade pip -r ${BUILD_DIR}/requirements.txt --target ${BUILD_DIR}

ADD bootstrap.yml .
ADD template.yml .
ADD version.yml .
ADD Makefile .