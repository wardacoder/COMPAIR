import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { ArrowRight, Sparkles } from "lucide-react";
import ThemeToggle from "../components/ThemeToggle";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-gradient-to-br from-blue-50 via-white to-sky-50 dark:from-slate-950 dark:via-slate-900 dark:to-black text-center px-6 overflow-hidden transition-colors duration-500">
      {/* Theme Toggle */}
      <ThemeToggle />

      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-400/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-gradient-to-r from-purple-300/15 to-pink-300/15 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Logo/Icon */}
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ duration: 0.6, type: "spring" }}
          className="mb-6"
        >
          <div className="inline-flex items-center justify-center p-6 bg-gradient-to-r from-blue-600 to-sky-500 rounded-3xl shadow-2xl">
            <Sparkles className="w-16 h-16 text-white" />
          </div>
        </motion.div>

        {/* Title */}
        <motion.h1
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-5xl sm:text-7xl font-extrabold mb-4"
        >
          <span className="bg-gradient-to-r from-blue-600 to-sky-500 bg-clip-text text-transparent">
            COMP
          </span>
          <span className="bg-gradient-to-r from-purple-500 to-pink-400 bg-clip-text text-transparent">
            AI
          </span>
          <span className="bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent">
            R
          </span>
        </motion.h1>

        {/* Tagline */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.4 }}
          className="text-gray-600 dark:text-gray-300 text-xl sm:text-2xl max-w-3xl mx-auto mb-12 leading-relaxed"
        >
          <span className="font-bold text-gray-800 dark:text-gray-100">Smart comparisons for smarter choices</span>
          <br />
          Compare gadgets, cars, tech, destinations, shows or anything that matters to you
        </motion.p>

        {/* CTA Button */}
        <motion.button
          onClick={() => navigate("/compare")}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.7, delay: 0.6 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="group inline-flex items-center gap-3 bg-gradient-to-r from-blue-600 to-sky-500 hover:from-blue-700 hover:to-sky-600 text-white px-10 py-5 rounded-full text-xl font-bold shadow-2xl hover:shadow-3xl transition-all duration-300"
        >
          Get Started
          <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
        </motion.button>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-4xl mx-auto"
        >
          <div className="p-6 bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-gray-200 dark:border-slate-700 hover:shadow-xl transition-all duration-300">
            <div className="text-4xl mb-3">🏆</div>
            <h3 className="font-bold text-gray-800 dark:text-gray-100 mb-2">
              Personalized Winners
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Get recommendations based on YOUR priorities
            </p>
          </div>

          <div className="p-6 bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-gray-200 dark:border-slate-700 hover:shadow-xl transition-all duration-300">
            <div className="text-4xl mb-3">🔗</div>
            <h3 className="font-bold text-gray-800 dark:text-gray-100 mb-2">
              Shareable Links
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Share comparisons with friends & family
            </p>
          </div>

          <div className="p-6 bg-white/50 dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-gray-200 dark:border-slate-700 hover:shadow-xl transition-all duration-300">
            <div className="text-4xl mb-3">💬</div>
            <h3 className="font-bold text-gray-800 dark:text-gray-100 mb-2">
              AI Follow-ups
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Ask questions about your comparisons
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}