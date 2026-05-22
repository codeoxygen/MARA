export default function Greeting({ user = 'Marketer', mode = 'centered' }) {
  return (
    <div className={`greeting ${mode === 'centered' ? 'centered' : 'header-style'}`}>
      <div className="hello">Hello, {user}</div>
      <div className="prompt">How can I assist you today?</div>
    </div>
  )
}
