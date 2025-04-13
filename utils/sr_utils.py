{
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "fTu3NQjAdJv6"
      },
      "source": [
        "Code for **super-resolution** (figures $1$ and $5$ from main paper).. Change `factor` to $8$ to reproduce images from fig. $9$ from supmat.\n",
        "\n",
        "You can play with parameters and see how they affect the result."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": 1,
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "YXk_wIcCdJwB",
        "outputId": "528a7386-34a2-46d4-f573-31018932b7ba"
      },
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "Cloning into 'deep-image-prior'...\n",
            "remote: Enumerating objects: 289, done.\u001b[K\n",
            "remote: Total 289 (delta 0), reused 0 (delta 0), pack-reused 289 (from 1)\u001b[K\n",
            "Receiving objects: 100% (289/289), 24.28 MiB | 18.94 MiB/s, done.\n",
            "Resolving deltas: 100% (155/155), done.\n"
          ]
        }
      ],
      "source": [
        "\"\"\"\n",
        "*Uncomment if running on colab*\n",
        "Set Runtime -> Change runtime type -> Under Hardware Accelerator select GPU in Google Colab\n",
        "\"\"\"\n",
        "!git clone https://github.com/DmitryUlyanov/deep-image-prior\n",
        "!mv deep-image-prior/* ./"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "-i-WLEgydJwF"
      },
      "source": [
        "# Import libs"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": 3,
      "metadata": {
        "id": "b0GftgCldJwH"
      },
      "outputs": [],
      "source": [
        "from __future__ import print_function\n",
        "import matplotlib.pyplot as plt\n",
        "%matplotlib inline\n",
        "\n",
        "import argparse\n",
        "import os\n",
        "# os.environ['CUDA_VISIBLE_DEVICES'] = '1'\n",
        "\n",
        "import numpy as np\n",
        "from models import *\n",
        "\n",
        "import torch\n",
        "import torch.optim\n",
        "\n",
        "from skimage.metrics import peak_signal_noise_ratio as psnr\n",
        "from models.downsampler import Downsampler\n",
        "\n",
        "from utils.sr_utils import *\n",
        "\n",
        "torch.backends.cudnn.enabled = True\n",
        "torch.backends.cudnn.benchmark =True\n",
        "dtype = torch.cuda.FloatTensor\n",
        "\n",
        "imsize = -1\n",
        "factor = 4 # 8\n",
        "enforse_div32 = 'CROP' # we usually need the dimensions to be divisible by a power of two (32 in this case)\n",
        "PLOT = True\n",
        "\n",
        "# To produce images from the paper we took *_GT.png images from LapSRN viewer for corresponding factor,\n",
        "# e.g. x4/zebra_GT.png for factor=4, and x8/zebra_GT.png for factor=8\n",
        "path_to_image = 'data/sr/zebra_GT.png'"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "TLT8pu0adJwI"
      },
      "source": [
        "# Load image and baselines"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": 9,
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/",
          "height": 367
        },
        "id": "4X5BOcwXdJwJ",
        "outputId": "abcbff3b-9f18-4ed8-f3a8-f86db407635a"
      },
      "outputs": [
        {
          "output_type": "error",
          "ename": "AttributeError",
          "evalue": "module 'PIL.Image' has no attribute 'ANTIALIAS'",
          "traceback": [
            "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
            "\u001b[0;31mAttributeError\u001b[0m                            Traceback (most recent call last)",
            "\u001b[0;32m<ipython-input-9-add94f1ba588>\u001b[0m in \u001b[0;36m<cell line: 0>\u001b[0;34m()\u001b[0m\n\u001b[1;32m      1\u001b[0m \u001b[0;31m# Starts here\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m----> 2\u001b[0;31m \u001b[0mimgs\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mload_LR_HR_imgs_sr\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mpath_to_image\u001b[0m \u001b[0;34m,\u001b[0m \u001b[0mimsize\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mfactor\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0menforse_div32\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m      3\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      4\u001b[0m \u001b[0mimgs\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m'bicubic_np'\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mimgs\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m'sharp_np'\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mimgs\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m'nearest_np'\u001b[0m\u001b[0;34m]\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mget_baselines\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mimgs\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m'LR_pil'\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mimgs\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m'HR_pil'\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      5\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n",
            "\u001b[0;32m/content/utils/sr_utils.py\u001b[0m in \u001b[0;36mload_LR_HR_imgs_sr\u001b[0;34m(fname, imsize, factor, enforse_div32)\u001b[0m\n\u001b[1;32m     52\u001b[0m     ]\n\u001b[1;32m     53\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m---> 54\u001b[0;31m     \u001b[0mimg_LR_pil\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mimg_HR_pil\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mresize\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mLR_size\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mImage\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mLANCZOS\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m     55\u001b[0m     \u001b[0mimg_LR_np\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mpil_to_np\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mimg_LR_pil\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m     56\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n",
            "\u001b[0;31mAttributeError\u001b[0m: module 'PIL.Image' has no attribute 'ANTIALIAS'"
          ]
        }
      ],
      "source": [
        "# Starts here\n",
        "imgs = load_LR_HR_imgs_sr(path_to_image , imsize, factor, enforse_div32)\n",
        "\n",
        "imgs['bicubic_np'], imgs['sharp_np'], imgs['nearest_np'] = get_baselines(imgs['LR_pil'], imgs['HR_pil'])\n",
        "\n",
        "if PLOT:\n",
        "    plot_image_grid([imgs['HR_np'], imgs['bicubic_np'], imgs['sharp_np'], imgs['nearest_np']], 4,12);\n",
        "    print ('PSNR bicubic: %.4f   PSNR nearest: %.4f' %  (\n",
        "                                        compare_psnr(imgs['HR_np'], imgs['bicubic_np']),\n",
        "                                        compare_psnr(imgs['HR_np'], imgs['nearest_np'])))"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "lYicDCCidJwK"
      },
      "source": [
        "# Set up parameters and net"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "9MYjCqbDdJwK"
      },
      "outputs": [],
      "source": [
        "input_depth = 32\n",
        "\n",
        "INPUT =     'noise'\n",
        "pad   =     'reflection'\n",
        "OPT_OVER =  'net'\n",
        "KERNEL_TYPE='lanczos2'\n",
        "\n",
        "LR = 0.01\n",
        "tv_weight = 0.0\n",
        "\n",
        "OPTIMIZER = 'adam'\n",
        "\n",
        "if factor == 4:\n",
        "    num_iter = 2000\n",
        "    reg_noise_std = 0.03\n",
        "elif factor == 8:\n",
        "    num_iter = 4000\n",
        "    reg_noise_std = 0.05\n",
        "else:\n",
        "    assert False, 'We did not experiment with other factors'"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "htOPgRGYdJwL"
      },
      "outputs": [],
      "source": [
        "net_input = get_noise(input_depth, INPUT, (imgs['HR_pil'].size[1], imgs['HR_pil'].size[0])).type(dtype).detach()\n",
        "\n",
        "NET_TYPE = 'skip' # UNet, ResNet\n",
        "net = get_net(input_depth, 'skip', pad,\n",
        "              skip_n33d=128,\n",
        "              skip_n33u=128,\n",
        "              skip_n11=4,\n",
        "              num_scales=5,\n",
        "              upsample_mode='bilinear').type(dtype)\n",
        "\n",
        "# Losses\n",
        "mse = torch.nn.MSELoss().type(dtype)\n",
        "\n",
        "img_LR_var = np_to_torch(imgs['LR_np']).type(dtype)\n",
        "\n",
        "downsampler = Downsampler(n_planes=3, factor=factor, kernel_type=KERNEL_TYPE, phase=0.5, preserve_size=True).type(dtype)"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "TaSClRXddJwM"
      },
      "source": [
        "# Define closure and optimize"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "HvKM1PXEdJwN"
      },
      "outputs": [],
      "source": [
        "def closure():\n",
        "    global i, net_input\n",
        "\n",
        "    if reg_noise_std > 0:\n",
        "        net_input = net_input_saved + (noise.normal_() * reg_noise_std)\n",
        "\n",
        "    out_HR = net(net_input)\n",
        "    out_LR = downsampler(out_HR)\n",
        "\n",
        "    total_loss = mse(out_LR, img_LR_var)\n",
        "\n",
        "    if tv_weight > 0:\n",
        "        total_loss += tv_weight * tv_loss(out_HR)\n",
        "\n",
        "    total_loss.backward()\n",
        "\n",
        "    # Log\n",
        "    psnr_LR = compare_psnr(imgs['LR_np'], torch_to_np(out_LR))\n",
        "    psnr_HR = compare_psnr(imgs['HR_np'], torch_to_np(out_HR))\n",
        "    print ('Iteration %05d    PSNR_LR %.3f   PSNR_HR %.3f' % (i, psnr_LR, psnr_HR), '\\r', end='')\n",
        "\n",
        "    # History\n",
        "    psnr_history.append([psnr_LR, psnr_HR])\n",
        "\n",
        "    if PLOT and i % 100 == 0:\n",
        "        out_HR_np = torch_to_np(out_HR)\n",
        "        plot_image_grid([imgs['HR_np'], imgs['bicubic_np'], np.clip(out_HR_np, 0, 1)], factor=13, nrow=3)\n",
        "\n",
        "    i += 1\n",
        "\n",
        "    return total_loss"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "q1nG_BFxdJwN"
      },
      "outputs": [],
      "source": [
        "psnr_history = []\n",
        "net_input_saved = net_input.detach().clone()\n",
        "noise = net_input.detach().clone()\n",
        "\n",
        "i = 0\n",
        "p = get_params(OPT_OVER, net, net_input)\n",
        "optimize(OPTIMIZER, p, closure, LR, num_iter)"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "1nE8PYHjdJwO"
      },
      "outputs": [],
      "source": [
        "out_HR_np = np.clip(torch_to_np(net(net_input)), 0, 1)\n",
        "result_deep_prior = put_in_center(out_HR_np, imgs['orig_np'].shape[1:])\n",
        "\n",
        "# For the paper we acually took `_bicubic.png` files from LapSRN viewer and used `result_deep_prior` as our result\n",
        "plot_image_grid([imgs['HR_np'],\n",
        "                 imgs['bicubic_np'],\n",
        "                 out_HR_np], factor=4, nrow=1);"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {
        "id": "cwd-MTAUdJwP"
      },
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
      "version": "3.6.9"
    },
    "colab": {
      "provenance": []
    }
  },
  "nbformat": 4,
  "nbformat_minor": 0
}