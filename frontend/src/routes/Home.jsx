export default function Home() {
  return (
    <div className="mt-12 flex flex-col items-center justify-center text-center min-h-[60vh]">
      <h1 className="text-5xl font-extrabold text-blue-700 mb-4">
        Welcome to <span className="text-yellow-500">BirdTag</span>
      </h1>
      <p className="text-xl text-gray-600 max-w-2xl mb-6">
        Effortlessly upload, tag, and explore bird media with our smart, serverless AWS-powered system.
      </p>

      <div className="flex flex-col sm:flex-row gap-4 mt-4">
        <a
          href="/signup"
          className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-xl text-lg font-semibold transition"
        >
          Get Started
        </a>
        <a
          href="/signin"
          className="border border-blue-600 hover:bg-blue-100 text-blue-600 px-6 py-3 rounded-xl text-lg font-semibold transition"
        >
          Sign In
        </a>
      </div>
    </div>
  );
}