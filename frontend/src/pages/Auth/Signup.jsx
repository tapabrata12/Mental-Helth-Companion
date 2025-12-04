import { useState } from "react";
import { Link } from "react-router-dom"
import NavIcon from '../../components/NavBar/NavIcon';
import { useNavigate } from 'react-router-dom';


const Signup = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: sign up logic
    navigate('/user-details');
  };

  return (
    <div className="relative min-h-screen bg-[#050A18] text-white overflow-hidden font-sans">
      {/* Navbar */}
      <NavIcon />

      {/* Container with a thin white rounded border and inner dark panel */}
      <div className="mx-6 mt-28">
        {/* Outer subtle white border using a 1px padded gradient wrapper to get a crisp rounded white edge */}
        <div className="rounded-2xl p-[1.5px]">
          {/* Inner panel */}
          <div className="bg-[#0a0f1d] rounded-2xl px-6 py-8 md:px-10 md:py-10">
            <div className="max-w-7xl mx-auto">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
                {/* Left: Copy */}
                <div className="lg:col-span-2">
                  <h2 className="text-2xl lg:text-3xl font-extrabold tracking-tight mb-4">
                    Create your Account
                  </h2>
                  <p className="text-sm text-white/70 max-w-lg">
                    Join NeuroMind and get personalized mental helth support. <br />
                    Create your account today.
                  </p>
                </div>

                {/* Right: Form */}
                <form
                  onSubmit={handleSubmit}
                  className="mt-6 lg:mt-0 flex flex-col gap-4"
                  aria-label="Signup form"
                >
                  <label className="sr-only" htmlFor="email">Email</label>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    placeholder="Email address"
                    className="w-full bg-transparent border border-white/20 rounded-xl px-4 py-3 placeholder-white/50 text-white focus:outline-none focus:ring-2 focus:ring-violet-400 focus:border-violet-400 transition"
                  />

                  <label className="sr-only" htmlFor="password">Password</label>
                  <input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    placeholder="Create a password"
                    className="w-full bg-transparent border border-white/20 rounded-xl px-4 py-3 placeholder-white/50 text-white focus:outline-none focus:ring-2 focus:ring-violet-400 focus:border-violet-400 transition"
                  />

                  {/* CTA — gradient pill with soft glow to match hero */}
                  <div className="flex items-center gap-4 pt-1">
                    <button
                      type="submit"
                      className="px-8 py-2 bg-linear-to-r from-yellow-500 to-violet-500 rounded-full font-semibold text-white shadow-[0_0_20px_rgba(234,88,12,0.5)] hover:shadow-[0_0_30px_rgba(234,88,12,0.7)] hover:scale-105 transition-all duration-300 cursor-pointer"
                    >
                      Signup
                    </button>

                    {/* Secondary action to match hero style but toned down */}
                    <Link
                      to="/login"
                      className="px-4 py-2 rounded-full text-sm font-medium border border-white/10 text-white/90 hover:bg-white/5 transition"
                    >
                      Already have an account?
                    </Link>
                  </div>

                  {/* Small helper text */}
                  <p className="text-xs text-white/60 mt-2">
                    By signing up you agree to our <span className="text-white/80 underline">Terms</span> & <span className="text-white/80 underline">Privacy</span>.
                  </p>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div> {/* mx-6 */}
    </div>
  );
};

export default Signup;
