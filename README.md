# SecuLive


현재 안면 인식 부분만 작성되었으며 sample에서 제공하는 caffe 모델과 텐서 플로우 모델이 들어감
얼굴 인식 하는 부분을 ROI로 지정 <- ROI 지정과 마스킹 모두 완료

딥러닝을 이용하여 개발 진행중. 데이터셋은 Flickr-Faces-HQ Dataset (FFHQ) 사용함 (https://github.com/NVlabs/ffhq-dataset)


해야할 일

1. 각 ROI 영역에서 처음 식별한 ROI에 특정 고유 이름을 붙여 식별을 유지하도록 함
  - 현재 User와 그 외의 얼굴 식별 가능하도록 모델 학습중.
  - 결과에 따라 결정
2. 처음 객체(0번)을 제외한 얼굴은 모두 블러 처리

plus - ROI에 이미지 합성하는 방법 pdf ch08의 도전과제 참조 할 것. 구현 가능함


끝난 일
1. 얼굴 인식 - SSD sample을 이용하여 구현.
2. 얼굴 인식을 ROI로 지정하는 것
3. 지정 부위 마스킹
