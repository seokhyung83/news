# news setting
Step1. Docker image - https://ngc.nvidia.com/catalog/containers/nvidia:rapidsai:rapidsai/tags

Step2. Chrome Setting - https://somjang.tistory.com/entry/Ubuntu-Ubuntu-%EC%84%9C%EB%B2%84%EC%97%90-Selenium-%EC%84%A4%EC%B9%98%ED%95%98%EA%B3%A0-%EC%82%AC%EC%9A%A9%ED%95%98%EA%B8%B0

Step3. apt-get install git-lfs & git clone https://huggingface.co/kykim/bertshared-kor-base  (https://huggingface.co/kykim/bertshared-kor-base)

Step4. pip install - torch, selenium, bs4, pororo
(Caution : You need to install gcc for running pororo.)
* Ref - Konlpy, Jpype 설치 후 JVM(Java Home Path 설정) https://zetawiki.com/wiki/%EB%A6%AC%EB%88%85%EC%8A%A4_$JAVA_HOME_%ED%99%98%EA%B2%BD%EB%B3%80%EC%88%98_%EC%84%A4%EC%A0%95
* Ref - Pororo 설치 시 marisa-trie error 발생 시, 다음 명령어 실행. sudo apt install gcc python3-dev python3-pip libxml2-dev libxslt1-dev zlib1g-dev g++

Step5. Mecab 설치
https://kogun82.tistory.com/173
* Ref - Pip install python-mecab-ko 설치 시 /opt/conda/envs/rapids/bin/mecab-config 심볼릭 링크 후 설치 https://www.lesbonscomptes.com/recoll/pages/recoll-korean.ko.html
