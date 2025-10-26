import React from 'react'
import ReactDOM from 'react-dom/client'
import { withStreamlitConnection, Streamlit } from 'streamlit-component-lib'
import App from './App'
import './style.css'

// 包装以自动处理与 Streamlit 的通信
const Wrapped = withStreamlitConnection(App)

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <Wrapped />
  </React.StrictMode>
)

// 告知 Streamlit：组件可用，并自适应高度
Streamlit.setComponentReady()
Streamlit.setFrameHeight()
