import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider, createBrowserRouter } from 'react-router-dom'
import { AuthProvider } from './hooks/useAuth'
import App from './App'
import HomePage from './pages/HomePage'
import LogPage from './pages/LogPage'
import PostPage from './pages/PostPage'
import AboutPage from './pages/AboutPage'
import LoginPage from './pages/LoginPage'
import WritePage from './pages/WritePage'
import MinePage from './pages/MinePage'
import './styles/global.css'

// React Router 6：App 为布局路由，页面为子路由（history 路由，Nginx 需配回退）
const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'log', element: <LogPage /> },
      { path: 'post/:id', element: <PostPage /> },
      { path: 'about', element: <AboutPage /> },
      { path: 'login', element: <LoginPage /> },
      { path: 'write/:id?', element: <WritePage /> },
      { path: 'mine', element: <MinePage /> },
      { path: '*', element: <div className="empty">这一页被海风吹走了</div> },
    ],
  },
])

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <RouterProvider router={router} />
      </AuthProvider>
    </QueryClientProvider>
  </StrictMode>,
)
