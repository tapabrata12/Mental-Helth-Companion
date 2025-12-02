import {BrowserRouter,Routes,Route} from 'react-router-dom';
import LandingPage from '../pages/Home/LandingPage';
import Login from '../pages/Auth/Login';
import Signup from '../pages/Auth/Signup';

const AppRouter = () => {
  return (
    <BrowserRouter>
      <Routes>
        
        {/* The default path "/" renders the LandingPage */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

      </Routes>
    </BrowserRouter>
  )
}

export default AppRouter