// Vercel 배포 때 실행된다: 환경 변수 API_BASE_URL 값으로 config.js 를 만든다.
// (Vercel 설정의 Build Command 에 `node build.js` 를 넣는다)
const fs = require("fs");

const apiBaseUrl = process.env.API_BASE_URL;
if (!apiBaseUrl) {
  console.error("환경 변수 API_BASE_URL 이 없습니다. Vercel 프로젝트 설정에서 추가하세요.");
  process.exit(1);
}

fs.writeFileSync("config.js", `window.API_BASE_URL = ${JSON.stringify(apiBaseUrl)};\n`);
console.log(`config.js 생성 완료: ${apiBaseUrl}`);
