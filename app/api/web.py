from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import settings

router = APIRouter(
    tags=["Web Interface"]
)

# 템플릿 설정
templates = Jinja2Templates(directory="templates")


def is_debug_enabled():
    """디버그 모드인지 확인"""
    if not settings.debug:
        raise HTTPException(
            status_code=403, 
            detail="Web admin interface is only available in development mode"
        )
    return True


@router.get("/admin", response_class=HTMLResponse, dependencies=[Depends(is_debug_enabled)])
async def database_admin(request: Request):
    """
    데이터베이스 관리 웹 인터페이스
    DEBUG 모드에서만 접근 가능
    """
    return templates.TemplateResponse("db_admin.html", {"request": request})


@router.get("/", response_class=HTMLResponse)
async def root_web(request: Request):
    """
    메인 웹 페이지
    """
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{settings.app_name}</title>
        <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --toss-blue: #0064FF;
                --toss-light-blue: #E5F2FF;
                --toss-red: #FF5A5A;
                --toss-light-red: #FFEBEB;
                --toss-gray-900: #191F28;
                --toss-gray-800: #333D4B;
                --toss-gray-700: #4E5968;
                --toss-gray-600: #6B7684;
                --toss-gray-500: #8B95A1;
                --toss-gray-400: #B0B8C1;
                --toss-gray-300: #C9CDD2;
                --toss-gray-200: #E5E8EB;
                --toss-gray-100: #F2F4F6;
                --toss-gray-50: #F9FAFB;
                --white: #FFFFFF;
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
                background-color: var(--toss-gray-50);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 24px;
                line-height: 1.6;
            }}
            
            .container {{
                background: var(--white);
                border-radius: 24px;
                padding: 48px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
                border: 1px solid var(--toss-gray-200);
                text-align: center;
                max-width: 720px;
                width: 100%;
            }}
            
            .logo {{
                width: 80px;
                height: 80px;
                background: var(--toss-blue);
                border-radius: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 32px;
                margin: 0 auto 24px;
                color: white;
            }}
            
            h1 {{
                color: var(--toss-gray-900);
                margin-bottom: 8px;
                font-size: 32px;
                font-weight: 700;
            }}
            
            .version {{
                color: var(--toss-gray-600);
                margin-bottom: 24px;
                font-size: 16px;
            }}
            
            .status {{
                display: inline-block;
                background: #E8F5E8;
                color: #2E7D2E;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 24px;
                border: 1px solid #4CAF50;
            }}
            
            .description {{
                color: var(--toss-gray-700);
                margin-bottom: 40px;
                line-height: 1.6;
                font-size: 16px;
            }}
            
            .links {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 16px;
                margin-top: 32px;
            }}
            
            .link-card {{
                background: var(--white);
                color: var(--toss-gray-800);
                padding: 24px;
                border-radius: 16px;
                text-decoration: none;
                transition: all 0.2s ease;
                border: 1px solid var(--toss-gray-200);
                position: relative;
            }}
            
            .link-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
                border-color: var(--toss-blue);
            }}
            
            .link-card h3 {{
                margin-bottom: 8px;
                font-size: 16px;
                font-weight: 600;
                color: var(--toss-gray-900);
            }}
            
            .link-card p {{
                font-size: 14px;
                color: var(--toss-gray-600);
            }}
            
            .admin-link {{
                background: var(--toss-light-red);
                border-color: var(--toss-red);
            }}
            
            .admin-link:hover {{
                border-color: var(--toss-red);
                box-shadow: 0 8px 24px rgba(255, 90, 90, 0.2);
            }}
            
            .admin-link h3 {{
                color: var(--toss-red);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🚀</div>
            <h1>{settings.app_name}</h1>
            <div class="version">버전 {settings.app_version}</div>
            <div class="status">서비스 운영 중</div>
            
            <div class="description">
                LLM 기반 개인화 소주제 생성 및 5단계 난이도별 동적 커리큘럼/아티클 생성을 지원하는 
                고성능 학습 API 서버입니다.
            </div>
            
            <div class="links">
                <a href="/docs" class="link-card">
                    <h3>API 문서</h3>
                    <p>Swagger UI로 API 테스트</p>
                </a>
                
                <a href="/redoc" class="link-card">
                    <h3>API 스펙</h3>
                    <p>ReDoc 형태의 상세 문서</p>
                </a>
                
                <a href="/health" class="link-card">
                    <h3>헬스체크</h3>
                    <p>서비스 상태 확인</p>
                </a>
                
                <a href="/levels" class="link-card">
                    <h3>난이도 정보</h3>
                    <p>5단계 학습 난이도</p>
                </a>
                
                {"" if not settings.debug else '''
                <a href="/admin" class="link-card admin-link">
                    <h3>DB 관리</h3>
                    <p>데이터베이스 관리 패널</p>
                </a>
                '''}
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)