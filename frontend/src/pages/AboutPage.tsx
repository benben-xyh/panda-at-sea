/** AboutPage —— 关于本志 */
export default function AboutPage() {
  return (
    <>
      <div className="ink-title"><h1>关 于</h1><span className="stamp">ABOUT</span></div>
      <div className="about-card">
        <div className="about-flex">
          <img src="/mascot.png" alt="手绘小熊猫头像" />
          <div>
            <p>「熊猫海上」是一本手绘小志——一只小熊猫划着小船，把每天遇到的小事记在笔记本上。</p>
            <p>
              这里没有热搜、没有推送、没有广告，只有慢慢写的字和慢慢画的线。灵感来自{' '}
              <a href="https://100r.co" target="_blank" rel="noreferrer" style={{ color: 'var(--accent)' }}>100r.co</a>
              ：两个人、一条帆船、一堆自给自足的小工具——互联网也可以是很小很温柔的地方。
            </p>
            <p>
              v2 版前端是 React + TypeScript（Vite 构建），后端是 Python FastAPI + PostgreSQL——
              看见喜欢的字，贴一张便签再走。
            </p>
          </div>
        </div>
      </div>
    </>
  )
}
