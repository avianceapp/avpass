-- CreateTable
CREATE TABLE "User" (
    "id" STRING NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "email" STRING NOT NULL,
    "password" STRING NOT NULL,
    "username" STRING,
    "active" BOOL NOT NULL DEFAULT true,
    "admin" BOOL NOT NULL DEFAULT false,
    "is_authenticated" BOOL NOT NULL DEFAULT true,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");
