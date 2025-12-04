import {BrowserRouter,Routes,Route} from 'react-router-dom';
import LandingPage from '../pages/Home/LandingPage';
import Login from '../pages/Auth/Login';
import Signup from '../pages/Auth/Signup';
import UserDetailsForm from '../pages/Profile/UserDetailsForm';

const AppRouter = () => {
  return (
    <BrowserRouter>
      <Routes>
        
        {/* The default path "/" renders the LandingPage */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/user-details" element={<UserDetailsForm />} />

      </Routes>
    </BrowserRouter>
  )
}

export default AppRouter