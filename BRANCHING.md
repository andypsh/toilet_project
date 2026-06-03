# 브랜치 전략

이 레포는 4단계 GitFlow 변형을 사용합니다.

```
main                  ← 출시용 (보호됨, 직접 푸시 금지)
  ↑ PR
dev                   ← 통합 개발 브랜치
  ↑ PR
  ├─ feature_andy     ← @andypsh 작업 공간
  └─ feature_dodo     ← @dododo9511 작업 공간
```

## 누가 어디서 작업?

| 사람 | 작업 브랜치 |
|---|---|
| @andypsh | `feature_andy` |
| @dododo9511 | `feature_dodo` |

## 표준 작업 흐름

### 1. 본인 브랜치로 가기
```bash
git checkout feature_andy        # 또는 feature_dodo
git pull origin feature_andy     # 원격에서 최신 받기
```

### 2. 작업 + 커밋
```bash
# 코드 수정
git add .
git commit -m "구체적인 변경 내용"
git push origin feature_andy
```

### 3. dev로 머지 (PR)
1. GitHub에서 `feature_andy` → `dev` 로 Pull Request 생성
2. 본인 (or 친구)이 리뷰
3. Merge

### 4. main으로 출시 (PR)
1. `dev`가 안정됐을 때 `dev` → `main` PR 생성
2. 리뷰 + 머지
3. main 머지 = 출시 가능 상태

## 충돌 피하는 팁

### feature_andy에 dev의 최신 변경 가져오기
다른 사람(feature_dodo)이 dev에 머지한 변경을 본인 feature 브랜치에 반영:
```bash
git checkout feature_andy
git fetch origin
git merge origin/dev
# 충돌 있으면 해결 후
git push origin feature_andy
```

### 같은 파일 동시 수정 방지
- **Andy**: 안드로이드 앱 코드 (`app/`)
- **Dodo**: 데이터 수집 파이프라인 (`collectors/`, `*.py`)
- 공통 (`README`, `docs/`, `BRANCHING.md`): 사전 협의

이렇게 영역을 나누면 충돌 거의 안 남.

## 절대 하지 말 것

❌ `main` 에 직접 push  
❌ `dev` 에 직접 push (PR로만)  
❌ 다른 사람의 feature 브랜치에 push  
❌ `git push --force` on main/dev  

## GitHub Branch Protection (관리자가 설정)

레포 Settings → Branches → Add rule 에서:

### `main` 보호
- ✅ Require a pull request before merging
- ✅ Require approvals (1명)
- ✅ Do not allow bypassing the above settings
- ✅ Restrict pushes that create matching branches

### `dev` 보호
- ✅ Require a pull request before merging
- ✅ Require approvals (1명)

## 첫 PR 만드는 법 (GitHub 웹)

1. https://github.com/andypsh/toilet_project 접속
2. **Pull requests** 탭 → **New pull request**
3. **base:** `dev` (받는 쪽)
4. **compare:** `feature_andy` (보내는 쪽)
5. 제목/설명 작성 → **Create pull request**
6. 리뷰어 본인 또는 친구 지정
7. 머지 클릭

## 자주 쓰는 명령어 치트시트

```bash
# 현재 브랜치 확인
git status

# 브랜치 목록 (원격 포함)
git branch -a

# 원격 변경사항 받아오기
git fetch origin

# 로컬 브랜치에 원격 최신 머지
git pull origin <브랜치명>

# 다른 브랜치로 이동
git checkout <브랜치명>

# 새 브랜치 만들고 이동
git checkout -b <새-브랜치명>

# 마지막 커밋 메시지 수정 (push 전에만)
git commit --amend -m "새 메시지"

# 변경사항 일시 보관 (다른 브랜치로 이동하기 전)
git stash
git stash pop  # 돌아와서 복원
```
