{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 61,
   "metadata": {},
   "outputs": [],
   "source": [
    "#Load libraries\n",
    "import os\n",
    "import numpy as np\n",
    "import torch\n",
    "import glob\n",
    "import torch.nn as nn\n",
    "from torchvision.transforms import transforms\n",
    "from torch.utils.data import DataLoader\n",
    "from torch.optim import Adam\n",
    "from torch.autograd import Variable\n",
    "import torchvision\n",
    "import pathlib"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 62,
   "metadata": {},
   "outputs": [],
   "source": [
    "#checking for device\n",
    "device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 63,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "cuda\n"
     ]
    }
   ],
   "source": [
    "print(device)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 64,
   "metadata": {},
   "outputs": [],
   "source": [
    "#Transforms\n",
    "transformer=transforms.Compose([\n",
    "    transforms.Resize((150,150)),\n",
    "    transforms.RandomHorizontalFlip(),\n",
    "    transforms.ToTensor(),  #0-255 to 0-1, numpy to tensors\n",
    "    transforms.Normalize([0.5,0.5,0.5], # 0-1 to [-1,1] , formula (x-mean)/std\n",
    "                        [0.5,0.5,0.5])\n",
    "])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 65,
   "metadata": {},
   "outputs": [],
   "source": [
    "#Dataloader\n",
    "\n",
    "#Path for training and testing directory\n",
    "train_path='/home/user/Desktop/pytorch_projects/scene_detection/seg_train/seg_train'\n",
    "test_path='/home/user/Desktop/pytorch_projects/scene_detection/seg_test/seg_test'\n",
    "\n",
    "train_loader=DataLoader(\n",
    "    torchvision.datasets.ImageFolder(train_path,transform=transformer),\n",
    "    batch_size=64, shuffle=True\n",
    ")\n",
    "test_loader=DataLoader(\n",
    "    torchvision.datasets.ImageFolder(test_path,transform=transformer),\n",
    "    batch_size=32, shuffle=True\n",
    ")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 66,
   "metadata": {},
   "outputs": [],
   "source": [
    "#categories\n",
    "root=pathlib.Path(train_path)\n",
    "classes=sorted([j.name.split('/')[-1] for j in root.iterdir()])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 67,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "['buildings', 'forest', 'glacier', 'mountain', 'sea', 'street']\n"
     ]
    }
   ],
   "source": [
    "print(classes)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 68,
   "metadata": {},
   "outputs": [],
   "source": [
    "#CNN Network\n",
    "\n",
    "\n",
    "class ConvNet(nn.Module):\n",
    "    def __init__(self,num_classes=6):\n",
    "        super(ConvNet,self).__init__()\n",
    "        \n",
    "        #Output size after convolution filter\n",
    "        #((w-f+2P)/s) +1\n",
    "        \n",
    "        #Input shape= (256,3,150,150)\n",
    "        \n",
    "        self.conv1=nn.Conv2d(in_channels=3,out_channels=12,kernel_size=3,stride=1,padding=1)\n",
    "        #Shape= (256,12,150,150)\n",
    "        self.bn1=nn.BatchNorm2d(num_features=12)\n",
    "        #Shape= (256,12,150,150)\n",
    "        self.relu1=nn.ReLU()\n",
    "        #Shape= (256,12,150,150)\n",
    "        \n",
    "        self.pool=nn.MaxPool2d(kernel_size=2)\n",
    "        #Reduce the image size be factor 2\n",
    "        #Shape= (256,12,75,75)\n",
    "        \n",
    "        \n",
    "        self.conv2=nn.Conv2d(in_channels=12,out_channels=20,kernel_size=3,stride=1,padding=1)\n",
    "        #Shape= (256,20,75,75)\n",
    "        self.relu2=nn.ReLU()\n",
    "        #Shape= (256,20,75,75)\n",
    "        \n",
    "        \n",
    "        \n",
    "        self.conv3=nn.Conv2d(in_channels=20,out_channels=32,kernel_size=3,stride=1,padding=1)\n",
    "        #Shape= (256,32,75,75)\n",
    "        self.bn3=nn.BatchNorm2d(num_features=32)\n",
    "        #Shape= (256,32,75,75)\n",
    "        self.relu3=nn.ReLU()\n",
    "        #Shape= (256,32,75,75)\n",
    "        \n",
    "        \n",
    "        self.fc=nn.Linear(in_features=75 * 75 * 32,out_features=num_classes)\n",
    "        \n",
    "        \n",
    "        \n",
    "        #Feed forwad function\n",
    "        \n",
    "    def forward(self,input):\n",
    "        output=self.conv1(input)\n",
    "        output=self.bn1(output)\n",
    "        output=self.relu1(output)\n",
    "            \n",
    "        output=self.pool(output)\n",
    "            \n",
    "        output=self.conv2(output)\n",
    "        output=self.relu2(output)\n",
    "            \n",
    "        output=self.conv3(output)\n",
    "        output=self.bn3(output)\n",
    "        output=self.relu3(output)\n",
    "            \n",
    "            \n",
    "            #Above output will be in matrix form, with shape (256,32,75,75)\n",
    "            \n",
    "        output=output.view(-1,32*75*75)\n",
    "            \n",
    "            \n",
    "        output=self.fc(output)\n",
    "            \n",
    "        return output\n",
    "            \n",
    "        \n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 69,
   "metadata": {},
   "outputs": [],
   "source": [
    "model=ConvNet(num_classes=6).to(device)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 70,
   "metadata": {},
   "outputs": [],
   "source": [
    "#Optmizer and loss function\n",
    "optimizer=Adam(model.parameters(),lr=0.001,weight_decay=0.0001)\n",
    "loss_function=nn.CrossEntropyLoss()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 71,
   "metadata": {},
   "outputs": [],
   "source": [
    "num_epochs=10"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 72,
   "metadata": {},
   "outputs": [],
   "source": [
    "#calculating the size of training and testing images\n",
    "train_count=len(glob.glob(train_path+'/**/*.jpg'))\n",
    "test_count=len(glob.glob(test_path+'/**/*.jpg'))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 73,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "14034 3000\n"
     ]
    }
   ],
   "source": [
    "print(train_count,test_count)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 75,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Epoch: 0 Train Loss: tensor(1.3346) Train Accuracy: 0.777967792503919 Test Accuracy: 0.7336666666666667\n",
      "Epoch: 1 Train Loss: tensor(0.6610) Train Accuracy: 0.8466581160039903 Test Accuracy: 0.72\n",
      "Epoch: 2 Train Loss: tensor(0.4469) Train Accuracy: 0.8867037195382642 Test Accuracy: 0.7073333333333334\n",
      "Epoch: 3 Train Loss: tensor(0.3311) Train Accuracy: 0.9115718968220037 Test Accuracy: 0.7053333333333334\n",
      "Epoch: 4 Train Loss: tensor(0.2717) Train Accuracy: 0.9249679350149637 Test Accuracy: 0.7256666666666667\n",
      "Epoch: 5 Train Loss: tensor(0.1466) Train Accuracy: 0.9590993301980903 Test Accuracy: 0.752\n",
      "Epoch: 6 Train Loss: tensor(0.1425) Train Accuracy: 0.9562491093059712 Test Accuracy: 0.755\n",
      "Epoch: 7 Train Loss: tensor(0.0998) Train Accuracy: 0.9713552800342027 Test Accuracy: 0.752\n",
      "Epoch: 8 Train Loss: tensor(0.1743) Train Accuracy: 0.9509762006555508 Test Accuracy: 0.7423333333333333\n",
      "Epoch: 9 Train Loss: tensor(0.1143) Train Accuracy: 0.9665811600399031 Test Accuracy: 0.744\n"
     ]
    }
   ],
   "source": [
    "#Model training and saving best model\n",
    "\n",
    "best_accuracy=0.0\n",
    "\n",
    "for epoch in range(num_epochs):\n",
    "    \n",
    "    #Evaluation and training on training dataset\n",
    "    model.train()\n",
    "    train_accuracy=0.0\n",
    "    train_loss=0.0\n",
    "    \n",
    "    for i, (images,labels) in enumerate(train_loader):\n",
    "        if torch.cuda.is_available():\n",
    "            images=Variable(images.cuda())\n",
    "            labels=Variable(labels.cuda())\n",
    "            \n",
    "        optimizer.zero_grad()\n",
    "        \n",
    "        outputs=model(images)\n",
    "        loss=loss_function(outputs,labels)\n",
    "        loss.backward()\n",
    "        optimizer.step()\n",
    "        \n",
    "        \n",
    "        train_loss+= loss.cpu().data*images.size(0)\n",
    "        _,prediction=torch.max(outputs.data,1)\n",
    "        \n",
    "        train_accuracy+=int(torch.sum(prediction==labels.data))\n",
    "        \n",
    "    train_accuracy=train_accuracy/train_count\n",
    "    train_loss=train_loss/train_count\n",
    "    \n",
    "    \n",
    "    # Evaluation on testing dataset\n",
    "    model.eval()\n",
    "    \n",
    "    test_accuracy=0.0\n",
    "    for i, (images,labels) in enumerate(test_loader):\n",
    "        if torch.cuda.is_available():\n",
    "            images=Variable(images.cuda())\n",
    "            labels=Variable(labels.cuda())\n",
    "            \n",
    "        outputs=model(images)\n",
    "        _,prediction=torch.max(outputs.data,1)\n",
    "        test_accuracy+=int(torch.sum(prediction==labels.data))\n",
    "    \n",
    "    test_accuracy=test_accuracy/test_count\n",
    "    \n",
    "    \n",
    "    print('Epoch: '+str(epoch)+' Train Loss: '+str(train_loss)+' Train Accuracy: '+str(train_accuracy)+' Test Accuracy: '+str(test_accuracy))\n",
    "    \n",
    "    #Save the best model\n",
    "    if test_accuracy>best_accuracy:\n",
    "        torch.save(model.state_dict(),'best_checkpoint.model')\n",
    "        best_accuracy=test_accuracy\n",
    "    \n",
    "       \n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
