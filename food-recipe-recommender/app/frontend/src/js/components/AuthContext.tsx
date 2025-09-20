// AuthContext.jsx
import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { getAuthStatus } from '../services/api';

type AuthContextType = {
    user: any;
    setUser: React.Dispatch<React.SetStateAction<any>>;
    loading: boolean;
    checkAuth: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType>({
    user: null,
    setUser: () => {},
    loading: true,
    checkAuth: async () => {}
});

export default function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = async () => {
        try {
            const data = await getAuthStatus();
            setUser(data.user);
        } catch (error) {
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    return (
        <AuthContext.Provider value={{ user, setUser, loading, checkAuth }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);