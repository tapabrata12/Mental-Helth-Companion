import LoginBtn from '../../components/Buttons/LoginBtn';
import SignupBtn from '../../components/Buttons/SignupBtn';
import NavIcon from '../../components/NavBar/NavIcon';
const LandingPage = () => {
  return (
    // Main Container
    <div className="relative min-h-screen bg-[#050A18] text-white overflow-hidden font-sans">

      {/* --- Background Ambient Glow Effects --- */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-purple-900/30 rounded-full blur-[128px] -translate-x-1/2 -translate-y-1/2"></div>
      <div className="absolute top-1/2 right-0 w-[500px] h-[500px] bg-orange-600/20 rounded-full blur-[128px] translate-x-1/3 -translate-y-1/2"></div>

      {/* --- Navbar --- */}
      <NavIcon />

      {/* --- Main Hero Content --- */}
      <main className="relative z-10 max-w-7xl mx-auto px-1 pt-5 lg:pt-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">

          {/* Left Column: Text */}
          <div className="space-y-8 text-center lg:text-left">
            <h1 className="text-5xl lg:text-7xl font-bold leading-tight tracking-tight">
              Illuminate Your <br />
              <span className="bg-clip-text text-transparent bg-linear-to-r from-white to-gray-400">
                Mind:
              </span> Journey to <br />
              Mental helth Wellness
            </h1>

            <p className="text-lg text-gray-300 max-w-xl mx-auto lg:mx-0 leading-relaxed">
              Compassionate care and innovative solutions for a brighter future.
              Discover the path to understanding your own potential.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">

              {/* Signup */}
              <SignupBtn />
              {/* Login */}
              <LoginBtn />
            </div>
          </div>

          {/* Right Column: Image */}
          <div className="relative flex justify-center lg:justify-end">

            <img
              src="/images/brain.png"
              alt="Glowing digital brain concept"
              // CHANGE 1: Removed 'mix-blend-multiply' (this fixes the face shadow)
              // CHANGE 2: Kept 'scale' and 'translate' to fix the gap you mentioned
              className="w-full max-w-lg lg:max-w-xl object-contain drop-shadow-2xl z-5 scale-110 lg:scale-125 lg:translate-x-10"
            />

            {/* Gradient overlay to smooth the bottom edge */}
            <div className="absolute inset-0 bg-linear-to-t from-[#050A18] via-transparent to-transparent pointer-events-none"></div>

          </div>

        </div>
      </main>
    </div>
  );
};

export default LandingPage;