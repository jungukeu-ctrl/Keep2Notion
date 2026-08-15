"""Google Master Token 최초 1회 획득 스크립트.

gkeepapi는 일반 아이디/비밀번호 로그인이 구글에 의해 차단되므로,
브라우저에서 발급받은 oauth_token을 master_token으로 교환한다.
자세한 절차는 README.md의 "Master Token 획득 방법" 참고.
"""
import sys

import gpsoauth

ANDROID_ID = "0000000000000000"


def main() -> None:
    email = input("Google 이메일: ").strip()
    oauth_token = input("브라우저에서 복사한 oauth_token (oauth2_4/...): ").strip()

    if not oauth_token.startswith("oauth2_4/"):
        print("경고: oauth_token 형식이 'oauth2_4/'로 시작하지 않습니다. 다시 확인하세요.")

    result = gpsoauth.exchange_token(email, oauth_token, ANDROID_ID)

    if "Token" not in result:
        print("토큰 교환 실패:", result)
        sys.exit(1)

    print("\nMaster Token 획득 성공. 아래 값을 .env의 GOOGLE_MASTER_TOKEN에 저장하세요:\n")
    print(result["Token"])


if __name__ == "__main__":
    main()
