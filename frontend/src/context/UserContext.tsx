import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';

export interface AuthUser {
  id: number;
  name: string;
  email: string;
}

interface UserContextType {
  userId: number;
  setUserId: (id: number) => void;
  userName: string;
  currentUser: AuthUser | null;
  loginUser: (user: AuthUser) => void;
  logoutUser: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);
const STORAGE_KEY = 'sahayakai_user';
const STORAGE_ID_KEY = 'sahayakai_user_id';

function readStoredUser(): AuthUser | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Partial<AuthUser>;
    if (!parsed.id || !parsed.name || !parsed.email) return null;
    return {
      id: Number(parsed.id),
      name: parsed.name,
      email: parsed.email,
    };
  } catch {
    return null;
  }
}

export const UserProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(() => readStoredUser());
  const [userId, setUserId] = useState<number>(() => readStoredUser()?.id ?? 1);

  useEffect(() => {
    if (currentUser) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(currentUser));
      localStorage.setItem(STORAGE_ID_KEY, String(currentUser.id));
      setUserId(currentUser.id);
    } else {
      localStorage.removeItem(STORAGE_KEY);
      localStorage.removeItem(STORAGE_ID_KEY);
      setUserId(1);
    }
  }, [currentUser]);

  const userName = currentUser?.name || `Student Developer (ID #${userId})`;

  const loginUser = (user: AuthUser) => {
    setCurrentUser(user);
  };

  const logoutUser = () => {
    setCurrentUser(null);
  };

  return (
    <UserContext.Provider value={{ userId, setUserId, userName, currentUser, loginUser, logoutUser }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = (): UserContextType => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};
