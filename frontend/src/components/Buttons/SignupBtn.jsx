import { Link } from 'react-router-dom';
const SignupBtn = () => {
    return (
        <Link to="/signup" className="px-8 py-4 bg-linear-to-r from-yellow-500 to-violet-500 rounded-full font-semibold text-white shadow-[0_0_20px_rgba(234,88,12,0.5)] hover:shadow-[0_0_30px_rgba(234,88,12,0.7)] hover:scale-105 transition-all duration-300 cursor-pointer">
            Get Started Today
        </Link>
    )
}

export default SignupBtn